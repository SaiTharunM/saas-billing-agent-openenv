import { execSync } from 'child_process';

try {
  console.log('Trying to ensurepip...');
  execSync('python3 -m ensurepip --upgrade');
  console.log('ensurepip successful');
} catch (err) {
  console.error('ensurepip failed:', err);
}
