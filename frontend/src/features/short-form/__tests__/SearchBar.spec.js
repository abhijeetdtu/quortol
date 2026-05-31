import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import SearchBar from '../components/SearchBar.vue'

describe('SearchBar', () => {
  it('emits search when keyword changes', async () => {
    const wrapper = mount(SearchBar, {
      props: {
        modelValue: '',
      },
    })

    await wrapper.find('input').setValue('match')
    await new Promise((resolve) => setTimeout(resolve, 350))

    const emitted = wrapper.emitted('search')
    expect(emitted).toBeTruthy()
  })
})
