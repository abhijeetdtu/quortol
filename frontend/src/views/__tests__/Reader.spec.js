import { mount } from '@vue/test-utils'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import Reader from '../Reader.vue'

const RSVPStub = {
  name: 'BlogRSVP',
  props: ['content'],
  template: '<div class="rsvp-stub">{{ content }}</div>',
  setup() {
    return { stop: vi.fn() }
  },
}

const settleFileRead = () => new Promise((resolve) => setTimeout(resolve, 20))

const dropFile = async (wrapper, file) => {
  await wrapper.get('.drop-zone').trigger('drop', {
    dataTransfer: { files: [file] },
  })
  await settleFileRead()
  await wrapper.vm.$nextTick()
}

describe('Reader', () => {
  beforeEach(() => {
    localStorage.clear()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('loads a UTF-8 text file locally and reports document metadata', async () => {
    const wrapper = mount(Reader, { global: { stubs: { BlogRSVP: RSVPStub } } })
    const file = new File(['\uFEFFone\r\ntwo three'], 'notes.txt', { type: 'text/plain' })

    await dropFile(wrapper, file)

    expect(wrapper.get('.rsvp-stub').text()).toBe('one\ntwo three')
    expect(wrapper.get('.document-summary').text()).toContain('notes.txt')
    expect(wrapper.get('.document-summary').text()).toContain('3 words')
    expect(wrapper.get('.document-summary').text()).toContain('1 sec at 300 WPM')
    expect(wrapper.text()).toContain('never uploaded')
  })

  it('supports selecting a file from the native input', async () => {
    const wrapper = mount(Reader, { global: { stubs: { BlogRSVP: RSVPStub } } })
    const input = wrapper.get('#reader-file')
    const file = new File(['selected text'], 'selected.txt', { type: 'text/plain' })
    Object.defineProperty(input.element, 'files', { configurable: true, value: [file] })

    await input.trigger('change')
    await settleFileRead()
    await wrapper.vm.$nextTick()

    expect(wrapper.text()).toContain('selected.txt')
    expect(wrapper.get('.rsvp-stub').text()).toBe('selected text')
  })

  it('rejects invalid, oversized, empty, and multiple files without replacing valid content', async () => {
    const wrapper = mount(Reader, { global: { stubs: { BlogRSVP: RSVPStub } } })
    await dropFile(wrapper, new File(['keep this'], 'valid.txt', { type: 'text/plain' }))

    await dropFile(wrapper, new File(['no'], 'invalid.md', { type: 'text/markdown' }))
    expect(wrapper.get('[role="alert"]').text()).toContain('.txt extension')
    expect(wrapper.text()).toContain('valid.txt')

    await dropFile(wrapper, new File([''], 'empty.txt', { type: 'text/plain' }))
    expect(wrapper.get('[role="alert"]').text()).toContain('empty')
    expect(wrapper.text()).toContain('valid.txt')

    const oversized = new File(['x'], 'large.txt', { type: 'text/plain' })
    Object.defineProperty(oversized, 'size', { value: (5 * 1024 * 1024) + 1 })
    await dropFile(wrapper, oversized)
    expect(wrapper.get('[role="alert"]').text()).toContain('5 MB')
    expect(wrapper.text()).toContain('valid.txt')

    await wrapper.get('.drop-zone').trigger('drop', {
      dataTransfer: {
        files: [
          new File(['a'], 'a.txt', { type: 'text/plain' }),
          new File(['b'], 'b.txt', { type: 'text/plain' }),
        ],
      },
    })
    expect(wrapper.get('[role="alert"]').text()).toContain('one .txt file')
    expect(wrapper.text()).toContain('valid.txt')
  })

  it('shows a read error without replacing valid content and clears on request', async () => {
    const wrapper = mount(Reader, { global: { stubs: { BlogRSVP: RSVPStub } } })
    await dropFile(wrapper, new File(['keep this'], 'valid.txt', { type: 'text/plain' }))

    const readAsText = vi.spyOn(FileReader.prototype, 'readAsText').mockImplementation(function fail() {
      this.onerror?.(new ProgressEvent('error'))
    })
    await dropFile(wrapper, new File(['broken'], 'broken.txt', { type: 'text/plain' }))

    expect(readAsText).toHaveBeenCalled()
    expect(wrapper.get('[role="alert"]').text()).toContain('could not be read')
    expect(wrapper.text()).toContain('valid.txt')

    await wrapper.get('.clear-button').trigger('click')
    expect(wrapper.find('.document-summary').exists()).toBe(false)
    expect(wrapper.find('.rsvp-stub').exists()).toBe(false)
  })

  it('keeps contextual selection and RSVP playback synchronized', async () => {
    const wrapper = mount(Reader)
    await dropFile(wrapper, new File(['one two three four'], 'context.txt', { type: 'text/plain' }))

    expect(wrapper.get('.context-section').isVisible()).toBe(true)
    expect(wrapper.get('[aria-current="true"]').text()).toBe('one')

    await wrapper.get('#rsvp-position').setValue('2')
    await wrapper.vm.$nextTick()
    expect(wrapper.get('.word').text()).toBe('three')
    expect(wrapper.get('[aria-current="true"]').text()).toBe('three')

    await wrapper.get('.rsvp-play').trigger('click')
    expect(wrapper.get('.context-section').isVisible()).toBe(false)

    await wrapper.get('.focus-exit').trigger('click')
    expect(wrapper.get('.context-section').isVisible()).toBe(true)
    expect(wrapper.get('[aria-current="true"]').text()).toBe('three')
  })

  it('stores filename and position and restores them when the same file is selected again', async () => {
    const file = new File(['one two three four'], 'resume.txt', { type: 'text/plain' })
    const first = mount(Reader)
    await dropFile(first, file)
    await first.get('#rsvp-position').setValue('2')

    expect(JSON.parse(localStorage.getItem('quortol-reader-progress'))).toEqual({
      fileName: 'resume.txt',
      wordIndex: 2,
    })
    first.unmount()

    const restored = mount(Reader)
    await restored.vm.$nextTick()
    expect(restored.text()).toContain('Re-select resume.txt to resume at word 3')
    await dropFile(restored, file)
    await restored.vm.$nextTick()

    expect(restored.get('.word').text()).toBe('three')
    expect(restored.get('[aria-current="true"]').text()).toBe('three')

    await restored.get('.clear-button').trigger('click')
    expect(localStorage.getItem('quortol-reader-progress')).toBeNull()
  })
})
