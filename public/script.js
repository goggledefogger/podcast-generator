const contentDiv = document.getElementById('content');
const podcastsLink = document.getElementById('podcasts-link');
const episodesLink = document.getElementById('episodes-link');

async function fetchPodcasts() {
  const response = await fetch('/api/podcasts');
  const podcasts = await response.json();
  return podcasts;
}

async function fetchEpisodes(podcastId) {
  const response = await fetch(`/api/podcasts/${podcastId}/episodes`);
  const episodes = await response.json();
  return episodes;
}

function renderPodcastsPage(podcasts) {
  contentDiv.innerHTML = '<h2>Podcasts</h2>';
  const podcastsList = document.createElement('ul');

  podcasts.forEach((podcast) => {
    const podcastItem = document.createElement('li');
    podcastItem.innerHTML = `
      ${podcast.name}
      <button onclick="handlePodcastEdit('${podcast.id}')">Edit</button>
      <button onclick="handlePodcastDelete('${podcast.id}')">Delete</button>
      <button onclick="renderCreateEpisodePage('${podcast.id}')">Create Episode</button>
      <ul id="episodes-list-${podcast.id}"></ul>
    `;
    podcastsList.appendChild(podcastItem);

    // Fetch and display episodes for this podcast
    fetchEpisodes(podcast.id).then((episodes) => {
      renderEpisodesForPodcast(episodes, podcast.id);
    });
  });

  const newPodcastForm = `
    <h3>Create New Podcast</h3>
    <form id="create-podcast-form">
      <input type="text" id="podcast-name" placeholder="Podcast Name" required>
      <button type="submit">Create Podcast</button>
    </form>
  `;

  contentDiv.appendChild(podcastsList);
  contentDiv.innerHTML += newPodcastForm;

  const createPodcastForm = document.getElementById('create-podcast-form');
  createPodcastForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    const podcastName = document.getElementById('podcast-name').value;
    const newPodcast = await createPodcast({ name: podcastName });
    console.log('Podcast created:', newPodcast);
    renderPodcastsPage(await fetchPodcasts()); // Refresh the podcasts list
  });
}

function renderEpisodesForPodcast(episodes, podcastId) {
  const episodesList = document.getElementById(`episodes-list-${podcastId}`);
  episodesList.innerHTML = ''; // Clear previous episodes

  episodes.forEach((episode) => {
    const episodeItem = document.createElement('li');
    episodeItem.innerHTML = `
      ${episode.topic}
      <button onclick="handleEpisodeDelete('${episode.id}', '${podcastId}')">Delete</button>
      <audio controls src="${episode.audio_file}"></audio>
    `;
    episodesList.appendChild(episodeItem);
  });
}

async function createPodcast(podcastData) {
  const response = await fetch('/api/podcasts', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(podcastData),
  });
  const podcast = await response.json();
  return podcast;
}

function renderEpisodesPage(episodes) {
  // Display the list of episodes with edit and delete buttons
  // Include a form for creating new episodes
}

async function handlePodcastDelete(podcastId) {
  // Send a DELETE request to remove the podcast
  // Refresh the podcasts list
}

async function handleEpisodeDelete(episodeId, podcastId) {
  try {
    const response = await fetch(`/api/episodes/${episodeId}`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    const data = await response.json();

    if (data.message === 'Episode deleted') {
      alert('Episode deleted successfully');
      // Optionally, refresh the episodes list or update the UI
      await loadPodcastEpisodes(podcastId);
    } else {
      alert('Failed to delete episode');
    }
  } catch (error) {
    console.error('Error:', error);
    alert('An error occurred while deleting the episode.');
  }
}

async function loadPodcastEpisodes(podcastId) {
  try {
    const response = await fetch(`/api/podcasts/${podcastId}/episodes`);
    const episodes = await response.json();
    // Update the UI with the new list of episodes
    displayEpisodes(episodes);
  } catch (error) {
    console.error('Error loading episodes:', error);
  }
}

function displayEpisodes(episodes) {
  // Your code to update the UI with the list of episodes
  const episodesList = document.getElementById('episodes-list');
  episodesList.innerHTML = '';

  episodes.forEach((episode) => {
    const episodeElement = document.createElement('div');
    episodeElement.innerHTML = `
            <p>${episode.title}</p>
            <button onclick="handleEpisodeDelete('${episode.id}', '${episode.podcastId}')">Delete</button>
        `;
    episodesList.appendChild(episodeElement);
  });
}


podcastsLink.addEventListener('click', async (event) => {
  event.preventDefault();
  const podcasts = await fetchPodcasts();
  renderPodcastsPage(podcasts);
});

episodesLink.addEventListener('click', async (event) => {
  event.preventDefault();
  const podcastId = 1; // Get the podcast ID from the selected podcast
  const episodes = await fetchEpisodes(podcastId);
  renderEpisodesPage(episodes);
});

async function createEpisode(podcastId, episodeData) {
    episodeData.podcast_id = podcastId;

    // Show the loader
    contentDiv.innerHTML = `<div class="loader"></div> Generating Episode...`;

    try {
        const response = await fetch("/api/episodes", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(episodeData)
        });
        const episode = await response.json();
        console.log("Episode created:", episode);

        // Hide the loader
        contentDiv.innerHTML = ''; // Clear the loader

    } catch (error) {
        // Handle errors and display an error message to the user
        console.error("Error creating episode:", error);
        contentDiv.innerHTML = "Error creating episode. Please try again.";
    }
}

function renderCreateEpisodePage(podcastId) {
  contentDiv.innerHTML = `
        <h2>Create Episode</h2>
        <form id="create-episode-form">
            <input type="text" id="topic" placeholder="Topic" required>
            <input type="number" id="num_speakers" placeholder="Number of Speakers" required>
            <input type="number" id="duration" placeholder="Duration (minutes)" required>
            <button type="submit">Create Episode</button>
        </form>
    `;

  const createEpisodeForm = document.getElementById('create-episode-form');
  createEpisodeForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    const topic = document.getElementById('topic').value;
    const num_speakers = parseInt(
      document.getElementById('num_speakers').value
    );
    const duration = parseInt(document.getElementById('duration').value);
    const episode = await createEpisode(podcastId, {
      topic,
      num_speakers,
      duration,
    });
    console.log('Episode created:', episode);
    // Refresh the episodes list or display the newly created episode
  });
}
