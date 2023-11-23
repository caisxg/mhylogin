getUuid = function () {
  for (var e = [], n = 0; n < 36; n++) e[n] = '0123456789abcdef'.substr(Math.floor(16 * Math.random()), 1)
  return (
    (e[14] = '4'),
    (e[19] = '0123456789abcdef'.substr((3 & e[19]) | 8, 1)),
    (e[8] = e[13] = e[18] = e[23] = '-'),
    (t = e.join('')),
    t
  )
}
getRandomNumber = function (t) {
  for (var e = '', n = t; n > 0; --n) e += '0123456789abcdef'[Math.floor(16 * Math.random())]
  return e
}
getRandomNumber10Radix = function (t) {
  for (var e = '', n = t; n > 0; --n) e += '0123456789'[Math.floor(10 * Math.random())]
  return e
}

// DEVICEFP_SEED_ID = getRandomNumber(16)
// DEVICEFP = getRandomNumber10Radix(10)
// DEVICEFP_SEED_TIME = String(Date.now())
// UUID = getUuid()
