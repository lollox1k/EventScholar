// src/components/ui/Input.js
import React from 'react';

export const Input = ({ type, placeholder, value, onChange, className }) => {
  return (
    <input
      type={type}
      placeholder={placeholder}
      value={value}
      onChange={onChange}
      className={`border border-gray-300 rounded-md ${className}`}
    />
  );
};