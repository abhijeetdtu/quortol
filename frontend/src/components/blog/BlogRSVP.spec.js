import { mount } from '@vue/test-utils'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import BlogRSVP from './BlogRSVP.vue'

describe('BlogRSVP', () => {
  beforeEach(() => {
    vi.useFakeTimers()
    localStorage.clear()
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  it('does not autoplay and advances one preserved token at a time', async () => {
    const wrapper = mount(BlogRSVP, { props: { content: 'Hello, RSVP world!' } })

    expect(wrapper.get('.word').text()).toBe('Hello,')
    expect(wrapper.get('.word-focus').text()).toBe('e')
    vi.advanceTimersByTime(1000)
    expect(wrapper.get('.word').text()).toBe('Hello,')

    await wrapper.get('.rsvp-play').trigger('click')
    expect(wrapper.emitted('playback-start')).toHaveLength(1)
    vi.advanceTimersByTime(300)
    await wrapper.vm.$nextTick()
    expect(wrapper.get('.word').text()).toBe('RSVP')
  })

  it('gives longer words progressively more display time', async () => {
    const wrapper = mount(BlogRSVP, {
      props: { content: 'a abcdef abcdefg abcdefghi abcdefghijk abcdefghijklmn done' },
    })

    await wrapper.get('.rsvp-play').trigger('click')

    vi.advanceTimersByTime(199)
    await wrapper.vm.$nextTick()
    expect(wrapper.get('.word').text()).toBe('a')
    vi.advanceTimersByTime(1)
    await wrapper.vm.$nextTick()
    expect(wrapper.get('.word').text()).toBe('abcdef')

    vi.advanceTimersByTime(200)
    await wrapper.vm.$nextTick()
    expect(wrapper.get('.word').text()).toBe('abcdefg')
    vi.advanceTimersByTime(225)
    await wrapper.vm.$nextTick()
    expect(wrapper.get('.word').text()).toBe('abcdefghi')
    vi.advanceTimersByTime(250)
    await wrapper.vm.$nextTick()
    expect(wrapper.get('.word').text()).toBe('abcdefghijk')
    vi.advanceTimersByTime(275)
    await wrapper.vm.$nextTick()
    expect(wrapper.get('.word').text()).toBe('abcdefghijklmn')
    vi.advanceTimersByTime(300)
    await wrapper.vm.$nextTick()
    expect(wrapper.get('.word').text()).toBe('done')
  })

  it('adds clause, sentence, quoted-sentence, and paragraph pauses', async () => {
    const wrapper = mount(BlogRSVP, {
      props: { content: 'go, next. "finished." paragraph\n\nbreak done' },
    })

    await wrapper.get('.rsvp-play').trigger('click')
    vi.advanceTimersByTime(299)
    await wrapper.vm.$nextTick()
    expect(wrapper.get('.word').text()).toBe('go,')
    vi.advanceTimersByTime(1)
    await wrapper.vm.$nextTick()
    expect(wrapper.get('.word').text()).toBe('next.')

    vi.advanceTimersByTime(399)
    await wrapper.vm.$nextTick()
    expect(wrapper.get('.word').text()).toBe('next.')
    vi.advanceTimersByTime(1)
    await wrapper.vm.$nextTick()
    expect(wrapper.get('.word').text()).toBe('"finished."')
    expect(wrapper.get('.word-focus').text()).toBe('n')

    vi.advanceTimersByTime(424)
    await wrapper.vm.$nextTick()
    expect(wrapper.get('.word').text()).toBe('"finished."')
    vi.advanceTimersByTime(1)
    await wrapper.vm.$nextTick()
    expect(wrapper.get('.word').text()).toBe('paragraph')
    vi.advanceTimersByTime(449)
    await wrapper.vm.$nextTick()
    expect(wrapper.get('.word').text()).toBe('paragraph')
    vi.advanceTimersByTime(1)
    await wrapper.vm.$nextTick()
    expect(wrapper.get('.word').text()).toBe('break')
  })

  it('splits words over 18 letters without advancing word-level progress', async () => {
    const wrapper = mount(BlogRSVP, {
      props: { content: 'abcdefghijklmnopqrs next' },
    })

    await wrapper.get('.rsvp-play').trigger('click')
    expect(wrapper.get('.word').text()).toBe('abcdefghijklmnopqr')
    expect(wrapper.get('.position-label').text()).toBe('Word 1 of 2')

    vi.advanceTimersByTime(300)
    await wrapper.vm.$nextTick()
    expect(wrapper.get('.word').text()).toBe('s')
    expect(wrapper.get('.position-label').text()).toBe('Word 1 of 2')
    expect(wrapper.emitted('position-change')).toBeUndefined()

    vi.advanceTimersByTime(200)
    await wrapper.vm.$nextTick()
    expect(wrapper.get('.word').text()).toBe('next')
    expect(wrapper.get('.position-label').text()).toBe('Word 2 of 2')
    expect(wrapper.emitted('position-change')).toEqual([[1]])

    wrapper.vm.seekTo(0)
    await wrapper.vm.$nextTick()
    expect(wrapper.get('.word').text()).toBe('abcdefghijklmnopqr')
  })

  it('recalculates adaptive total time when WPM changes', async () => {
    const wrapper = mount(BlogRSVP, { props: { content: 'a communication.' } })

    expect(wrapper.get('.rsvp-time').text()).toBe('0:00 / 0:01')
    await wrapper.get('#rsvp-speed').setValue('100')
    expect(wrapper.get('.rsvp-time').text()).toBe('0:00 / 0:02')
  })

  it('pauses, restarts, seeks, and reports accessible progress', async () => {
    const wrapper = mount(BlogRSVP, { props: { content: 'one two three four' } })
    const slider = wrapper.get('#rsvp-position')

    await slider.setValue('2')
    expect(wrapper.get('.word').text()).toBe('three')
    expect(slider.attributes('aria-valuetext')).toBe('Word 3 of 4')

    await wrapper.get('button:nth-of-type(2)').trigger('click')
    expect(wrapper.get('.word').text()).toBe('one')

    await wrapper.get('.rsvp-play').trigger('click')
    await wrapper.get('.rsvp-play').trigger('click')
    vi.advanceTimersByTime(1000)
    expect(wrapper.get('.word').text()).toBe('one')
  })

  it('emits position changes and exposes a paused external seek', async () => {
    const wrapper = mount(BlogRSVP, { props: { content: 'one two three four' } })

    await wrapper.get('.rsvp-play').trigger('click')
    wrapper.vm.seekTo(2)
    await wrapper.vm.$nextTick()

    expect(wrapper.get('.word').text()).toBe('three')
    expect(wrapper.classes()).not.toContain('is-focus-mode')
    expect(wrapper.emitted('playback-state').at(-1)).toEqual([false])
    expect(wrapper.emitted('position-change').at(-1)).toEqual([2])
  })

  it('persists a valid speed and restores it in another reader', async () => {
    const wrapper = mount(BlogRSVP, { props: { content: 'one two' } })
    await wrapper.get('#rsvp-speed').setValue('500')

    expect(localStorage.getItem('quortol-rsvp-wpm')).toBe('500')
    wrapper.unmount()

    const restored = mount(BlogRSVP, { props: { content: 'one two' } })
    await restored.vm.$nextTick()
    expect(restored.get('#rsvp-speed').element.value).toBe('500')
  })

  it('resets and clears playback when content changes or the component unmounts', async () => {
    const clearTimeoutSpy = vi.spyOn(window, 'clearTimeout')
    const wrapper = mount(BlogRSVP, { props: { content: 'old content here' } })
    await wrapper.get('.rsvp-play').trigger('click')
    await wrapper.setProps({ content: 'new article' })

    expect(wrapper.get('.word').text()).toBe('new')
    expect(wrapper.emitted('playback-state').at(-1)).toEqual([false])
    expect(clearTimeoutSpy).toHaveBeenCalled()
    wrapper.unmount()
  })

  it('uses a non-announcing word display and labeled native controls', () => {
    const wrapper = mount(BlogRSVP, { props: { content: 'accessible reader' } })

    expect(wrapper.get('.word-stage').attributes('aria-live')).toBe('off')
    expect(wrapper.get('label[for="rsvp-position"]').exists()).toBe(true)
    expect(wrapper.get('label[for="rsvp-speed"]').exists()).toBe(true)
  })

  it('enters distraction-free focus mode while playing and exits with Escape', async () => {
    const wrapper = mount(BlogRSVP, { props: { content: 'focus mode reader' } })

    await wrapper.get('.rsvp-play').trigger('click')
    expect(wrapper.classes()).toContain('is-focus-mode')
    expect(document.body.style.overflow).toBe('hidden')
    expect(wrapper.get('.focus-exit').attributes('aria-label')).toContain('exit focus mode')

    window.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape' }))
    await wrapper.vm.$nextTick()

    expect(wrapper.classes()).not.toContain('is-focus-mode')
    expect(document.body.style.overflow).toBe('')
  })
})
