import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import TagFilter from '../components/TagFilter.vue'

describe('TagFilter', () => {
  it('emits updated tags when option is selected', async () => {
    const wrapper = mount(TagFilter, {
      props: {
        modelValue: [],
        availableTags: ['#ipl', '#cricket'],
      },
    })

    await wrapper.find('input.filter-input').setValue('ipl')
    await wrapper.find('.dropdown-option').trigger('click')

    const emitted = wrapper.emitted('update:modelValue')
    expect(emitted).toBeTruthy()
    expect(emitted[0][0]).toContain('#ipl')
  })
})
