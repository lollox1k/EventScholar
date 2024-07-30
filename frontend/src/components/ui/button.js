// src/components/ui/Button.js
import React from 'react';

export const Button = ({ variant, children, className }) => {
  const baseStyle = 'px-4 py-2 font-semibold rounded-md';
  const outlineStyle = 'border border-blue-600 text-blue-600';
  const solidStyle = 'bg-blue-600 text-white';

  const variantStyle = variant === 'outline' ? outlineStyle : solidStyle;

  return (
    <button className={`${baseStyle} ${variantStyle} ${className}`}>
      {children}
    </button>
  );
};