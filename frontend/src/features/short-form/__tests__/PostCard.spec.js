import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import PostCard from '../components/PostCard.vue'

global.IntersectionObserver = class {
  observe() {}
  unobserve() {}
  disconnect() {}
}

describe('PostCard', () => {
  it('renders fallback when media fails', async () => {
    const wrapper = mount(PostCard, {
      props: {
        post: {
          id: '1',
          text: 'test',
          media_url: '/static/short_form/images/missing.jpg',
          video_url: null,
          author: 'A',
          timestamp: '2026-05-30T00:00:00Z',
          tags: ['#test'],
        },
      },
    })

    await wrapper.find('img').trigger('error')
    expect(wrapper.text()).toContain('Media unavailable')
  })
})
