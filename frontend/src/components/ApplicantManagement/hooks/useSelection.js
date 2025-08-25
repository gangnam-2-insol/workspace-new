import { useState, useCallback } from 'react';

export default function useSelection(initial = []) {
  const [selected, setSelected] = useState(initial);
  const toggle = id => setSelected(prev => prev.includes(id) ? prev.filter(i=>i!==id) : [...prev, id]);
  const clear = () => setSelected([]);
  const selectAll = allIds => setSelected(allIds);
  const isAll = allIds => allIds.every(id=>selected.includes(id));
  return { selected, toggle, clear, selectAll, isAll };
}

