import fetch from 'node-fetch';
import readline from 'readline';

// Define the API base URL and the token
const apiUrl = 'https://api.madgrades.com/v1/courses';
const apiToken = '492e91a9f7d74dbab647ec2bf11efd27';  // Use your own API token here

// Create a readline interface to accept input from the user
const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

// Function to fetch course data
async function fetchCourseDetails(courseQuery) {
  try {
    const response = await fetch(`${apiUrl}?query=${encodeURIComponent(courseQuery)}`, {
      method: 'GET',
      headers: {
        'Authorization': `Token token=${apiToken}`
      }
    });

    const data = await response.json();

    // Pick the first subject from the first result
    const firstResult = data.results[0];
    if (firstResult) {
      console.log(`Subject Name: ${firstResult.name}`);
      console.log(`Course Number: ${firstResult.number}`);
    } else {
      console.log('No results found.');
    }
  } catch (error) {
    console.error('Error fetching course data:', error);
  }
}

// Prompt the user for the course name
rl.question('Enter the course name: ', (courseQuery) => {
  fetchCourseDetails(courseQuery).then(() => rl.close());
});