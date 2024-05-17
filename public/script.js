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
      <button onclick="handlePodcastEdit(${podcast.id})">Edit</button>
      <button onclick="handlePodcastDelete(${podcast.id})">Delete</button>
      <button onclick="renderCreateEpisodePage(${podcast.id})">Create Episode</button>
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
      <button onclick="handleEpisodeEdit(${episode.id})">Edit</button>
      <button onclick="handleEpisodeDelete(${episode.id})">Delete</button>
      <button onclick="handleEpisodeRegenerate(${episode.id})">Regenerate</button>
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

async function handlePodcastEdit(podcastId) {
  // Fetch the podcast data and display a form for editing
  // On form submit, send a PUT request to update the podcast
}

async function handlePodcastDelete(podcastId) {
  // Send a DELETE request to remove the podcast
  // Refresh the podcasts list
}

async function handleEpisodeEdit(episodeId) {
  // Fetch the episode data and display a form for editing
  // On form submit, send a PUT request to update the episode
}

async function handleEpisodeDelete(episodeId) {
  // Send a DELETE request to remove the episode
  // Refresh the episodes list
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

// Add event listeners for edit and delete buttons
// ... (fetchPodcasts, fetchEpisodes, renderPodcastsPage, renderEpisodesPage, and other functions)

async function createEpisode(podcastId, episodeData) {
  episodeData.podcast_id = podcastId;
  const response = await fetch('/api/episodes', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(episodeData),
  });
  const episode = await response.json();
  return episode;
}

async function handleEpisodeRegenerate(episodeId) {
  const response = await fetch(`/api/episodes/${episodeId}/regenerate`, {
    method: 'POST',
  });
  const result = await response.json();
  console.log(result.message);
  // Refresh the episode data and display the updated content
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

// Add a button or link to create a new episode
// When clicked, call the renderCreateEpisodePage function with the selected podcast ID
