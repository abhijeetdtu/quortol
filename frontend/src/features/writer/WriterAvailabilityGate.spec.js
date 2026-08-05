import { flushPromises, mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const statusRequest = vi.fn()
vi.mock('../../services/api', () => ({
  writer: {
    status: (...args) => statusRequest(...args),
    autocomplete: vi.fn(),
  },
}))
vi.mock('./analysisStream', () => ({ streamWriterAnalysis: vi.fn() }))

import WriterAvailabilityGate from './WriterAvailabilityGate.vue'
import { resetWriterAvailability } from './availability'

describe('WriterAvailabilityGate', () => {
  beforeEach(() => {
    resetWriterAvailability()
    statusRequest.mockReset()
  })

  it('shows a loading state before the probe completes', () => {
    statusRequest.mockReturnValue(new Promise(() => {}))
    const wrapper = mount(WriterAvailabilityGate)
    expect(wrapper.text()).toContain('Checking Writing Assistant')
  })

  it('renders Writer when the backend is available', async () => {
    statusRequest.mockResolvedValue({ data: { available: true } })
    const wrapper = mount(WriterAvailabilityGate)
    await flushPromises()
    expect(wrapper.find('textarea').exists()).toBe(true)
  })

  it('renders the unavailable page when the backend is unavailable', async () => {
    statusRequest.mockResolvedValue({ data: { available: false } })
    const wrapper = mount(WriterAvailabilityGate)
    await flushPromises()
    expect(wrapper.text()).toContain('Writing Assistant is currently unavailable')
    expect(wrapper.find('textarea').exists()).toBe(false)
  })
})
