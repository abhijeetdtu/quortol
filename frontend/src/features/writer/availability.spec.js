import { beforeEach, describe, expect, it, vi } from 'vitest'

const statusRequest = vi.fn()
vi.mock('../../services/api', () => ({
  writer: { status: (...args) => statusRequest(...args) },
}))

import {
  checkWriterAvailability,
  resetWriterAvailability,
  writerAvailability,
} from './availability'

describe('writer availability', () => {
  beforeEach(() => {
    resetWriterAvailability()
    statusRequest.mockReset()
  })

  it('marks Writer available only for an explicit true response', async () => {
    statusRequest.mockResolvedValue({ data: { available: true } })
    await checkWriterAvailability()
    expect(writerAvailability.value).toBe('available')
  })

  it('treats unavailable and failed checks as unavailable', async () => {
    statusRequest.mockResolvedValueOnce({ data: { available: false } })
    await checkWriterAvailability()
    expect(writerAvailability.value).toBe('unavailable')

    resetWriterAvailability()
    statusRequest.mockRejectedValueOnce(new Error('secret upstream failure'))
    await checkWriterAvailability()
    expect(writerAvailability.value).toBe('unavailable')
  })

  it('deduplicates concurrent checks', async () => {
    let resolveRequest
    statusRequest.mockReturnValue(new Promise((resolve) => { resolveRequest = resolve }))
    const first = checkWriterAvailability()
    const second = checkWriterAvailability({ force: true })
    expect(statusRequest).toHaveBeenCalledTimes(1)
    resolveRequest({ data: { available: true } })
    await Promise.all([first, second])
  })
})
