export const stadiums = [
  {
    id: 'city_01',
    name: '광주기아챔피언스필드',
    homeTeam: 'KIA 타이거즈',
    lat: 35.1684282,
    lon: 126.888283,
  },
  {
    id: 'city_02',
    name: '대전한화생명볼파크',
    homeTeam: '한화 이글스',
    lat: 36.3171,
    lon: 127.4291,
  },
  {
    id: 'city_03',
    name: '수원KT위즈파크',
    homeTeam: 'KT 위즈',
    lat: 37.2997,
    lon: 127.0097,
  },
  {
    id: 'city_04',
    name: '창원NC파크',
    homeTeam: 'NC 다이노스',
    lat: 35.2225,
    lon: 128.5822,
  },
  {
    id: 'city_05',
    name: '대구삼성라이온즈파크',
    homeTeam: '삼성 라이온즈',
    lat: 35.8412,
    lon: 128.6816,
  },
  {
    id: 'city_06',
    name: '서울잠실야구장',
    homeTeam: 'LG 트윈스 · 두산 베어스',
    lat: 37.5122,
    lon: 127.0719,
  },
  {
    id: 'city_07',
    name: '인천SSG랜더스필드',
    homeTeam: 'SSG 랜더스',
    lat: 37.437,
    lon: 126.6933,
  },
  {
    id: 'city_08',
    name: '고척스카이돔',
    homeTeam: '키움 히어로즈',
    lat: 37.4983,
    lon: 126.8672,
  },
  {
    id: 'city_09',
    name: '부산사직야구장',
    homeTeam: '롯데 자이언츠',
    lat: 35.194,
    lon: 129.0615,
  },
]

export const findStadium = (stadiumId) => {
  return stadiums.find((stadium) => stadium.id === stadiumId)
}
