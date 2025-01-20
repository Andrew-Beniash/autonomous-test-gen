import { render, screen } from '@testing-library/react';
import App from '../../App';

describe('App Component', () => {
  it('renders the main layout correctly', () => {
    render(<App />);

    // Test main container
    const mainElement = screen.getByTestId('app-main');
    expect(mainElement).toBeInTheDocument();
    expect(mainElement).toHaveClass('min-h-screen bg-gray-100');

    // Test heading
    const headingElement = screen.getByRole('heading', { level: 1 });
    expect(headingElement).toBeInTheDocument();
    expect(headingElement).toHaveTextContent('Test Generation Platform');
  });

  it('applies correct styling classes', () => {
    render(<App />);

    // Test container styling
    const containerElement = screen.getByTestId('app-container');
    expect(containerElement).toHaveClass('container mx-auto px-4 py-8');
  });
});
