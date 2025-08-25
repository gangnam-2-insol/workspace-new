import styled from 'styled-components';

export const SearchBar = styled.div`
  background: white;
  border-radius: 16px;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  border: 1px solid var(--border-color);
`;

export const SearchSection = styled.div`
  display: flex;
  gap: 16px;
  align-items: center;
  margin-bottom: 16px;
  flex-wrap: wrap;
`;

export const SearchInputContainer = styled.div`
  position: relative;
  flex: 1;
  display: flex;
  align-items: center;
`;

export const SearchInput = styled.input.attrs({
  id: 'applicant-management-search-input'
})`
  flex: 1;
  padding: 12px 16px;
  padding-right: 40px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  font-size: 14px;
  outline: none;
  transition: all 0.2s ease;
  font-weight: 500;
  color: var(--text-primary);

  &::placeholder {
    color: var(--text-light);
    font-weight: 400;
  }

  &:hover {
    border-color: var(--primary-color);
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  }

  &:focus {
    border-color: var(--primary-color);
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
  }
`;

export const ClearButton = styled.button`
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  color: var(--text-secondary);
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;

  &:hover {
    background: var(--background-secondary);
    color: var(--text-primary);
  }

  &:active {
    transform: translateY(-50%) scale(0.95);
  }
`;

export const JobPostingSelect = styled.select.attrs({
  id: 'applicant-management-job-posting-select'
})`
  padding: 12px 16px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  font-size: 14px;
  outline: none;
  background: white;
  width: 250px;
  cursor: pointer;
  transition: all 0.2s ease;
  font-weight: 500;
  color: var(--text-primary);

  &:hover {
    border-color: var(--primary-color);
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  }

  &:focus {
    border-color: var(--primary-color);
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
  }

  option {
    padding: 8px 12px;
    font-size: 14px;
    background: white;
    color: var(--text-primary);

    &:hover {
      background: var(--background-secondary);
    }
  }

  option:first-child {
    font-weight: 600;
    color: var(--primary-color);
  }
`;

export const FilterButton = styled.button.attrs({
  id: 'applicant-management-filter-button'
})`
  padding: 12px 16px;
  background: ${props => props.hasActiveFilters ? 'var(--primary-color)' : 'white'};
  color: ${props => props.hasActiveFilters ? 'white' : 'var(--text-primary)'};
  border: 1px solid ${props => props.hasActiveFilters ? 'var(--primary-color)' : 'var(--border-color)'};
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s ease;

  &:hover {
    border-color: var(--primary-color);
    color: ${props => props.hasActiveFilters ? 'white' : 'var(--primary-color)'};
    background: ${props => props.hasActiveFilters ? 'var(--primary-dark)' : 'white'};
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  }

  &:focus {
    outline: none;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
  }
`;

export const FilterBadge = styled.span`
  background: ${props => props.hasActiveFilters ? 'white' : 'var(--primary-color)'};
  color: ${props => props.hasActiveFilters ? 'var(--primary-color)' : 'white'};
  border-radius: 50%;
  width: 18px;
  height: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 10px;
  font-weight: 600;
`;

export const ViewModeSection = styled.div`
  display: flex;
  gap: 8px;
  align-items: center;
`;

export const ViewModeButton = styled.button`
  padding: 8px 12px;
  background: ${props => props.active ? 'var(--primary-color)' : 'white'};
  color: ${props => props.active ? 'white' : 'var(--text-primary)'};
  border: 1px solid ${props => props.active ? 'var(--primary-color)' : 'var(--border-color)'};
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  font-weight: 500;
  transition: all 0.2s ease;

  &:hover {
    border-color: var(--primary-color);
    color: ${props => props.active ? 'white' : 'var(--primary-color)'};
    background: ${props => props.active ? 'var(--primary-dark)' : 'white'};
  }
`;
