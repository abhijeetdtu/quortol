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
    expect(wrapper.get('.word-focus').text()).toBe('l')
    vi.advanceTimersByTime(1000)
    expect(wrapper.get('.word').text()).toBe('Hello,')

    await wrapper.get('.rsvp-play').trigger('click')
    expect(wrapper.emitted('playback-start')).toHaveLength(1)
    vi.advanceTimersByTime(200)
    await wrapper.vm.$nextTick()
    expect(wrapper.get('.word').text()).toBe('RSVP')
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
