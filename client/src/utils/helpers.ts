/**
 * 테스트 타입 문자열을 사용자 친화적인 라벨로 변환합니다.
 * @param testType 테스트 타입 (예: 'cdi', 'rcmas', 'bdi')
 * @returns 변환된 라벨 문자열
 */
export const getTestTypeLabel = (testType: string): string => {
  if (!testType) return '알 수 없는 테스트';
  
  switch (testType.toLowerCase()) {
    case 'cdi': return 'CDI (아동 우울 척도)';
    case 'rcmas': return 'RCMAS (아동 불안 척도)';
    case 'bdi': return 'BDI (벡 우울 척도)';
    default: return testType.toUpperCase();
  }
};