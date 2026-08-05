import { readonly, ref } from 'vue'
import { writer } from '../../services/api'

const status = ref('unknown')
let pendingRequest = null

export const checkWriterAvailability = ({ force = false } = {}) => {
  if (pendingRequest) return pendingRequest
  if (!force && status.value !== 'unknown') return Promise.resolve(status.value)

  pendingRequest = writer.status()
    .then((response) => {
      status.value = response.data?.available === true ? 'available' : 'unavailable'
      return status.value
    })
    .catch(() => {
      status.value = 'unavailable'
      return status.value
    })
    .finally(() => {
      pendingRequest = null
    })
  return pendingRequest
}

export const writerAvailability = readonly(status)

export const resetWriterAvailability = () => {
  status.value = 'unknown'
  pendingRequest = null
}
