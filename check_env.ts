import { execSync } from 'child_process';

try {
  const pipVersion = execSync('pip --version').toString();
  console.log(`Pip version: ${pipVersion}`);
} catch (err) {
  console.error('Failed to check pip command:', err);
}
try {
  const pip3Version = execSync('pip3 --version').toString();
  console.log(`Pip3 version: ${pip3Version}`);
} catch (err) {
  console.error('Failed to check pip3 command:', err);
}
