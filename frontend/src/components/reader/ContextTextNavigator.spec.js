import { mount } from '@vue/test-utils'
import { afterEach, describe, expect, it, vi } from 'vitest'

import ContextTextNavigator from './ContextTextNavigator.vue'

describe('ContextTextNavigator', () => {
  afterEach(() => vi.restoreAllMocks())

  it('preserves the full text with one highlighted current word', () => {
    const content = 'one\n\ntwo three'
    const wrapper = mount(ContextTextNavigator, { props: { content, currentIndex: 1 } })

    expect(wrapper.get('.context-viewport').text()).toBe(content)
    expect(wrapper.get('[aria-current="true"]').text()).toBe('two')
    expect(wrapper.findAll('.context-word')).toHaveLength(1)
  })

  it('renders a large document with constant DOM complexity', () => {
    const content = Array.from({ length: 65000 }, (_, index) => `word${index}`).join(' ')
    const wrapper = mount(ContextTextNavigator, { props: { content, currentIndex: 3498 } })

    expect(wrapper.get('[aria-current="true"]').text()).toBe('word3498')
    expect(wrapper.findAll('.context-word')).toHaveLength(1)
    expect(wrapper.get('.context-viewport').text()).toBe(content)
  })

  it('maps a native text click to the corresponding RSVP word', async () => {
    const wrapper = mount(ContextTextNavigator, {
      attachTo: document.body,
      props: { content: 'one two three', currentIndex: 0 },
    })
    const trailingText = wrapper.get('.context-viewport').element.lastChild.firstChild
    const caretRangeFromPoint = vi.fn(() => ({ startContainer: trailingText, startOffset: 5 }))
    document.caretRangeFromPoint = caretRangeFromPoint

    await wrapper.get('.context-viewport').trigger('click', { clientX: 10, clientY: 10 })

    expect(wrapper.emitted('seek')).toEqual([[2]])
    wrapper.unmount()
  })

  it('centers the real highlighted element and respects reduced motion', async () => {
    vi.spyOn(window, 'matchMedia').mockReturnValue({ matches: true })
    const wrapper = mount(ContextTextNavigator, { props: { content: 'one two', currentIndex: 0 } })
    const first = wrapper.get('.context-word').element
    first.scrollIntoView = vi.fn()

    await wrapper.setProps({ currentIndex: 1 })
    await wrapper.vm.$nextTick()
    const second = wrapper.get('.context-word').element
    second.scrollIntoView = vi.fn()
    wrapper.vm.centerCurrentWord()
    await wrapper.vm.$nextTick()

    expect(second.scrollIntoView).toHaveBeenCalledWith({
      block: 'center',
      inline: 'nearest',
      behavior: 'auto',
    })
  })
})
