import { flushPromises, mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import Writer from '../Writer.vue'

const autocomplete = vi.fn()
const streamWriterAnalysis = vi.fn()
vi.mock('../../services/api', () => ({
  writer: { autocomplete: (...args) => autocomplete(...args) },
}))
vi.mock('../../features/writer/analysisStream', () => ({
  streamWriterAnalysis: (...args) => streamWriterAnalysis(...args),
}))

const emitSuccessfulAnalysis = async (payload, options) => {
  options.onEvent({ type: 'start', schema_version: '2.0' })
  options.onEvent({ type: 'block', block: { id: 'logical_consistency', title: 'Logical consistency', content: 'The premise holds.' } })
  options.onEvent({ type: 'block', block: { id: 'depth', title: 'Depth', content: '<script>unsafe()</script>' } })
  options.onEvent({ type: 'complete', completed_ids: ['logical_consistency', 'depth'], failed_ids: [] })
}

describe('Writer', () => {
  beforeEach(() => {
    localStorage.clear()
    autocomplete.mockReset()
    streamWriterAnalysis.mockReset()
    vi.spyOn(window, 'confirm').mockReturnValue(true)
  })

  it('shows autocomplete results and accepts the active result', async () => {
    autocomplete.mockResolvedValue({ data: { recommendations: [' one', ' two'] } })
    const wrapper = mount(Writer)
    const textarea = wrapper.find('textarea')
    await textarea.setValue('Start')
    textarea.element.setSelectionRange(5, 5)
    await textarea.trigger('keydown', { key: 'Tab' })
    await flushPromises()
    await textarea.trigger('keydown', { key: 'ArrowDown' })
    await textarea.trigger('keydown', { key: 'Enter' })
    expect(textarea.element.value).toBe('Start two')
  })

  it('restores the local draft and recommendation count', () => {
    localStorage.setItem('quortol.writer.draft.v1', JSON.stringify({ title: 'Draft', body: 'Saved body', count: 5 }))
    const wrapper = mount(Writer)
    expect(wrapper.find('.title-input').element.value).toBe('Draft')
    expect(wrapper.find('textarea').element.value).toBe('Saved body')
    expect(wrapper.find('select').element.value).toBe('5')
  })

  it('renders streamed prose blocks safely as they arrive', async () => {
    streamWriterAnalysis.mockImplementation(emitSuccessfulAnalysis)
    const wrapper = mount(Writer)
    await wrapper.find('.title-input').setValue('Draft')
    await wrapper.find('textarea').setValue('Complete prose')
    await wrapper.find('.analyze-button').trigger('click')
    await flushPromises()

    expect(streamWriterAnalysis).toHaveBeenCalledWith(
      { title: 'Draft', body: 'Complete prose' },
      expect.objectContaining({ signal: expect.any(AbortSignal), onEvent: expect.any(Function) }),
    )
    expect(wrapper.text()).toContain('The premise holds.')
    expect(wrapper.text()).toContain('<script>unsafe()</script>')
    expect(wrapper.html()).not.toContain('<script>unsafe()')
  })

  it('keeps the old analysis until the first new block arrives', async () => {
    streamWriterAnalysis.mockImplementationOnce(emitSuccessfulAnalysis)
    const wrapper = mount(Writer)
    const textarea = wrapper.find('textarea')
    await textarea.setValue('First version')
    await wrapper.find('.analyze-button').trigger('click')
    await flushPromises()

    let release
    streamWriterAnalysis.mockImplementationOnce(async (payload, options) => {
      options.onEvent({ type: 'start', schema_version: '2.0' })
      await new Promise((resolve) => { release = () => {
        options.onEvent({ type: 'block', block: { id: 'voice', title: 'Voice', content: 'New voice result.' } })
        options.onEvent({ type: 'complete', completed_ids: ['voice'], failed_ids: [] })
        resolve()
      } })
    })
    await textarea.setValue('Second version')
    await wrapper.find('.analyze-button').trigger('click')
    await flushPromises()
    expect(wrapper.text()).toContain('The premise holds.')
    release()
    await flushPromises()
    expect(wrapper.text()).not.toContain('The premise holds.')
    expect(wrapper.text()).toContain('New voice result.')
  })

  it('retains completed blocks and reports partial failures', async () => {
    streamWriterAnalysis.mockImplementation(async (payload, options) => {
      options.onEvent({ type: 'start', schema_version: '2.0' })
      options.onEvent({ type: 'block', block: { id: 'depth', title: 'Depth', content: 'Depth result.' } })
      options.onEvent({ type: 'step_error', id: 'imagery', message: 'Could not complete this section.' })
      options.onEvent({ type: 'complete', completed_ids: ['depth'], failed_ids: ['imagery'] })
    })
    const wrapper = mount(Writer)
    await wrapper.find('textarea').setValue('Draft text')
    await wrapper.find('.analyze-button').trigger('click')
    await flushPromises()
    expect(wrapper.text()).toContain('Depth result.')
    expect(wrapper.text()).toContain('imagery')
    expect(wrapper.text()).toContain('Retry')
  })

  it('marks streamed analysis stale after the draft changes', async () => {
    streamWriterAnalysis.mockImplementation(emitSuccessfulAnalysis)
    const wrapper = mount(Writer)
    const textarea = wrapper.find('textarea')
    await textarea.setValue('First version')
    await wrapper.find('.analyze-button').trigger('click')
    await flushPromises()
    await textarea.setValue('Second version')
    expect(wrapper.text()).toContain('Analysis of an earlier draft')
  })

  it('cancels an active stream', async () => {
    streamWriterAnalysis.mockImplementation(() => new Promise(() => {}))
    const wrapper = mount(Writer)
    await wrapper.find('textarea').setValue('Draft text')
    await wrapper.find('.analyze-button').trigger('click')
    const signal = streamWriterAnalysis.mock.calls[0][1].signal
    await wrapper.find('.document-toolbar .clear-button').trigger('click')
    expect(signal.aborted).toBe(true)
  })

  it('rejects an empty draft without starting a stream', async () => {
    const wrapper = mount(Writer)
    await wrapper.find('.analyze-button').trigger('click')
    expect(streamWriterAnalysis).not.toHaveBeenCalled()
    expect(wrapper.text()).toContain('Write something before requesting an analysis.')
  })
})
