export const teams = [
  { id: 'KIA', name: 'KIA 타이거즈', color: '#c8102e' },
  { id: 'SAMSUNG', name: '삼성 라이온즈', color: '#0066b3' },
  { id: 'LG', name: 'LG 트윈스', color: '#c30452' },
  { id: 'DOOSAN', name: '두산 베어스', color: '#131230' },
  { id: 'KT', name: 'KT 위즈', color: '#222222' },
  { id: 'SSG', name: 'SSG 랜더스', color: '#ce0e2d' },
  { id: 'LOTTE', name: '롯데 자이언츠', color: '#041e42' },
  { id: 'NC', name: 'NC 다이노스', color: '#315288' },
  { id: 'KIWOOM', name: '키움 히어로즈', color: '#820024' },
  { id: 'HANWHA', name: '한화 이글스', color: '#f37321' },
]

export const findTeam = (teamId) => {
  return teams.find((team) => team.id === teamId)
}
