import { render, screen } from '@testing-library/react';

function Smoke() {
  return <p>laravel-new smoke</p>;
}

test('renders smoke marker', () => {
  render(<Smoke />);
  expect(screen.getByText('laravel-new smoke')).toBeInTheDocument();
});
