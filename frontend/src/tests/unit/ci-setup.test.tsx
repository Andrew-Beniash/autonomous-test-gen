import { render, screen } from '@testing-library/react';
import App from '../../App';

test('basic render test', () => {
  render(<App />);
  // This assumes your App component renders something with this text
  const element = screen.getByText(/test generation/i);
  expect(element).toBeInTheDocument();
});

test('environment setup', () => {
  expect(process.env.NODE_ENV).toBeDefined();
});
