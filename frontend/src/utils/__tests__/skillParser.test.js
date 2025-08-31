/**
 * 스킬 파서 유틸리티 테스트
 */

import { parseSkills, formatSkills, isValidSkills, normalizeSkills } from '../skillParser';

describe('skillParser', () => {
  describe('parseSkills', () => {
    test('배열 형태의 스킬을 올바르게 파싱', () => {
      const skills = ['React', 'JavaScript', 'Node.js'];
      expect(parseSkills(skills)).toEqual(['React', 'JavaScript', 'Node.js']);
    });

    test('JSON 배열 문자열을 올바르게 파싱', () => {
      const skills = '["Agile", "Scrum", "SQL", "Google Analytics"]';
      expect(parseSkills(skills)).toEqual(['Agile', 'Scrum', 'SQL', 'Google Analytics']);
    });

    test('Python 리스트 형태 문자열을 올바르게 파싱', () => {
      const skills = "['Agile', 'Scrum', 'SQL', 'Google Analytics']";
      expect(parseSkills(skills)).toEqual(['Agile', 'Scrum', 'SQL', 'Google Analytics']);
    });

    test('쉼표로 구분된 문자열을 올바르게 파싱', () => {
      const skills = 'React, JavaScript, Node.js';
      expect(parseSkills(skills)).toEqual(['React', 'JavaScript', 'Node.js']);
    });

    test('단일 스킬 문자열을 올바르게 파싱', () => {
      const skills = 'React';
      expect(parseSkills(skills)).toEqual(['React']);
    });

    test('빈 문자열을 올바르게 처리', () => {
      expect(parseSkills('')).toEqual([]);
      expect(parseSkills('   ')).toEqual([]);
    });

    test('null/undefined를 올바르게 처리', () => {
      expect(parseSkills(null)).toEqual([]);
      expect(parseSkills(undefined)).toEqual([]);
    });

    test('따옴표가 포함된 스킬을 올바르게 처리', () => {
      const skills = "'React', 'JavaScript', 'Node.js'";
      expect(parseSkills(skills)).toEqual(['React', 'JavaScript', 'Node.js']);
    });
  });

  describe('formatSkills', () => {
    test('스킬을 올바르게 포맷팅', () => {
      const skills = ['React', 'JavaScript', 'Node.js', 'Python', 'Java'];
      const result = formatSkills(skills, 3);

      expect(result.displaySkills).toEqual(['React', 'JavaScript', 'Node.js']);
      expect(result.remainingCount).toBe(2);
      expect(result.totalCount).toBe(5);
      expect(result.allSkills).toEqual(['React', 'JavaScript', 'Node.js', 'Python', 'Java']);
    });

    test('최대 표시 개수보다 적은 스킬을 올바르게 처리', () => {
      const skills = ['React', 'JavaScript'];
      const result = formatSkills(skills, 5);

      expect(result.displaySkills).toEqual(['React', 'JavaScript']);
      expect(result.remainingCount).toBe(0);
      expect(result.totalCount).toBe(2);
    });
  });

  describe('isValidSkills', () => {
    test('유효한 스킬 데이터를 올바르게 검증', () => {
      expect(isValidSkills(['React', 'JavaScript'])).toBe(true);
      expect(isValidSkills("['React', 'JavaScript']")).toBe(true);
      expect(isValidSkills('React, JavaScript')).toBe(true);
    });

    test('무효한 스킬 데이터를 올바르게 검증', () => {
      expect(isValidSkills('')).toBe(false);
      expect(isValidSkills(null)).toBe(false);
      expect(isValidSkills(undefined)).toBe(false);
      expect(isValidSkills([])).toBe(false);
    });
  });

  describe('normalizeSkills', () => {
    test('스킬 배열을 올바르게 정규화', () => {
      const skills = ['React', 'JavaScript', 'Node.js'];
      expect(normalizeSkills(skills)).toEqual(['React', 'JavaScript', 'Node.js']);
    });

    test('따옴표가 포함된 스킬을 올바르게 정규화', () => {
      const skills = ["'React'", '"JavaScript"', 'Node.js'];
      expect(normalizeSkills(skills)).toEqual(['React', 'JavaScript', 'Node.js']);
    });

    test('빈 스킬을 올바르게 필터링', () => {
      const skills = ['React', '', 'JavaScript', null, 'Node.js'];
      expect(normalizeSkills(skills)).toEqual(['React', 'JavaScript', 'Node.js']);
    });
  });
});
