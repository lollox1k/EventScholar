// src/components/ui/Select.js
import React from 'react';

export const Select = ({ value, onValueChange, className, children }) => {
  return (
    <select
      value={value}
      onChange={(e) => onValueChange(e.target.value)}
      className={`border border-gray-300 rounded-md ${className}`}
    >
      {children}
    </select>
  );
};