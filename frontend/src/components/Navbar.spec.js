import { mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

vi.mock('../stores/auth', () => ({
  useAuthStore: () => ({ isAuthenticated: false, user: null, logout: vi.fn() }),
}))
const statusRequest = vi.fn()
vi.mock('../services/api', () => ({
  auth: { logout: vi.fn() },
  writer: { status: (...args) => statusRequest(...args) },
}))

import Navbar from './Navbar.vue'
import { checkWriterAvailability, resetWriterAvailability } from '../features/writer/availability'

const mountNavbar = () => mount(Navbar, {
  global: {
    stubs: {
      RouterLink: { props: ['to'], template: '<a :href="to"><slot /></a>' },
    },
  },
})

describe('Navbar Writer availability', () => {
  beforeEach(() => {
    resetWriterAvailability()
    statusRequest.mockReset()
  })

  it('hides Writer while availability is unknown or unavailable', async () => {
    const wrapper = mountNavbar()
    expect(wrapper.text()).not.toContain('Writer')
    statusRequest.mockResolvedValue({ data: { available: false } })
    await checkWriterAvailability()
    await wrapper.vm.$nextTick()
    expect(wrapper.text()).not.toContain('Writer')
  })

  it('shows Writer only when the backend is available', async () => {
    const wrapper = mountNavbar()
    statusRequest.mockResolvedValue({ data: { available: true } })
    await checkWriterAvailability()
    await wrapper.vm.$nextTick()
    expect(wrapper.text()).toContain('Writer')
    expect(wrapper.find('a[href="/writer"]').exists()).toBe(true)
  })
})
