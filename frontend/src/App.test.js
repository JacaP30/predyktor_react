import { render, screen } from '@testing-library/react';
import App from './App';

test('renderuje ekran startowy gdy brak zapisanej konfiguracji', () => {
  localStorage.clear();
  render(<App />);
  expect(screen.getByRole('dialog')).toBeInTheDocument();
  expect(screen.getByText(/Wybierz sposób korzystania/i)).toBeInTheDocument();
});
