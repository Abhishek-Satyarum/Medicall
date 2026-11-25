import api from './api'

export const getDoctors = () =>
  api.get('/doctors').then(({ data }) => data)

export const getSpecialties = () =>
  api.get('/specialties').then(({ data }) => data)
