import React, { useEffect, useState, useRef } from 'react';
import { GoogleLogin } from '@react-oauth/google';
import '../App.css';
import VideoCard from '../components/VideoCard';
import BottomNavbar from '../components/BottomNavbar';
import TopNavbar from '../components/TopNavbar';
import Posts from '../API/api';

// This array holds information about different videos
const videoUrls = [
  {
    url: require('../videos/video1.mp4'),
    profilePic: 'https://p16-sign-useast2a.tiktokcdn.com/tos-useast2a-avt-0068-giso/9d429ac49d6d18de6ebd2a3fb1f39269~c5_100x100.jpeg?x-expires=1688479200&x-signature=pjH5pwSS8Sg1dJqbB1GdCLXH6ew%3D',
    username: 'csjackie',
    description: 'Lol nvm #compsci #chatgpt #ai #openai #techtok',
    song: 'Original sound - Famed Flames',
    likes: 430,
    comments: 13,
    saves: 23,
    shares: 1,
  },
  {
    url: require('../videos/video2.mp4'),
    profilePic: 'https://p16-sign-va.tiktokcdn.com/tos-maliva-avt-0068/eace3ee69abac57c39178451800db9d5~c5_100x100.jpeg?x-expires=1688479200&x-signature=wAkVmwL7lej15%2B16ypSWQOqTP8s%3D',
    username: 'dailydotdev',
    description: 'Every developer brain @francesco.ciulla #developerjokes #programming #programminghumor #programmingmemes',
    song: 'tarawarolin wants you to know this isnt my sound - Chaplain J Rob',
    likes: '13.4K',
    comments: 3121,
    saves: 254,
    shares: 420,
  },
  {
    url: require('../videos/video3.mp4'),
    profilePic: 'https://p77-sign-va.tiktokcdn.com/tos-maliva-avt-0068/4e6698b235eadcd5d989a665704daf68~c5_100x100.jpeg?x-expires=1688479200&x-signature=wkwHDKfNuIDqIVHNm29%2FRf40R3w%3D',
    username: 'wojciechtrefon',
    description: '#programming #softwareengineer #vscode #programmerhumor #programmingmemes',
    song: 'help so many people are using my sound - Ezra',
    likes: 5438,
    comments: 238,
    saves: 12,
    shares: 117,
  },
  {
    url: require('../videos/video4.mp4'),
    profilePic: 'https://p16-sign-va.tiktokcdn.com/tos-maliva-avt-0068/4bda52cf3ad31c728153859262c329db~c5_100x100.jpeg?x-expires=1688486400&x-signature=ssUbbCpZFJj6uj33D%2BgtcqxMvgQ%3D',
    username: 'faruktutkus',
    description: 'Wait for the end | Im RTX 4090 TI | #softwareengineer #softwareengineer #coding #codinglife #codingmemes ',
    song: 'orijinal ses - Computer Science',
    likes: 9689,
    comments: 230,
    saves: 1037,
    shares: 967,
  },
];


function FeedComponent({ user }) {
  
  const [videos, setVideos] = useState([]);
  const videoRefs = useRef([]);

  useEffect(() => {
    async function fetchData() {

      debugger
      const feed = new Posts(user.access_token);
      const videoUrls = await feed.getPosts();
      setVideos(videoUrls);
    }
    fetchData();
  }, []);

  useEffect(() => {
    const observerOptions = {
      root: null,
      rootMargin: '0px',
      threshold: 0.8, 
    };

    // This function handles the intersection of videos
    const handleIntersection = (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          const videoElement = entry.target;
          videoElement.play();
        } else {
          const videoElement = entry.target;
          videoElement.pause();
        }
      });
    };

    const observer = new IntersectionObserver(handleIntersection, observerOptions);

    // We observe each video reference to trigger play/pause
    videoRefs.current.forEach((videoRef) => {
      observer.observe(videoRef);
    });

    // We disconnect the observer when the component is unmounted
    return () => {
      observer.disconnect();
    };
  }, [videos]);

  // This function handles the reference of each video
  const handleVideoRef = (index) => (ref) => {
    videoRefs.current[index] = ref;
  };

  return (
    <>
      <TopNavbar className="top-navbar" />
        {videos.map((video, index) => (
          <VideoCard
          key={index}
          username={video.username}
          description={video.caption}
          song={video.song || `Original Sound - ${video.username}`}
          likes={video.likes}
          saves={video.saves}
          comments={video.comments}
          shares={video.reposts}
          url={'http://127.0.0.1:8000' + video.video}
          profilePic={video.profilePic}
          setVideoRef={handleVideoRef(index)}
          autoplay={index === 0}
          />
        ))}
      <BottomNavbar className="bottom-navbar" />
    </>
  );
}


function UploadComponent({ user, file, setIsUserUploading }) {
  const [fileToUpload, setFileToUpload] = useState(file);
  const [caption, setCaption] = useState('');
  const [isPremium, setIsPremium] = useState(false);

  const handleFileInputChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile && selectedFile.type === 'video/mp4') {
      document.getElementById('caption').value = selectedFile.name;
      console.log('Selected file:', selectedFile);
      setFileToUpload(selectedFile);
    } else {
      e.target.value = null;
      alert('Please select an MP4 file.');
    }
  };

  useEffect(() => {
    if (file) {
      document.getElementById('caption').value = file.name;
    }
  }, [file]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    const feed = new Posts(user.access_token);
    await feed.uploadPost(fileToUpload, caption, isPremium); // Assuming uploadPost takes the file, caption, and isPremium as parameters
    setIsUserUploading(false)
  };

  return (
    <>
      <form>
        <h1 className="text-center">Upload</h1>
        <input
          id="caption" // Add an id to the caption input for easy access
          className="w-100 mb-3"
          name="caption"
          placeholder="A caption to your video"
          value={caption}
          onChange={(e) => setCaption(e.target.value)}
        />
        <label className="w-100 mb-3">
          {/* Use a label to wrap the file input */}
          Choose an MP4 video:
          <input
            type="file"
            name="video"
            className="w-100 mb-3"
            accept="video/mp4" // Accept only MP4 files
            onChange={handleFileInputChange}
          />
        </label>
        <input
          id="premiumcheckbox"
          className="mb-3"
          type="checkbox"
          name="Premium"
          placeholder="Premium video"
          checked={isPremium}
          onChange={(e) => setIsPremium(e.target.checked)}
        />
        <label htmlFor="premiumcheckbox">Premium Video</label>

        <button className="primary w-100 mb-2" onClick={handleSubmit}>
          Upload Video
        </button>
        <button className="warn w-100" onClick={() => setIsUserUploading(false)}>
          Cancel
        </button>
      </form>
    </>
  );
}


function ScrollFeedPage({ user }) {
  const [isUserUploading, setIsUserUploading] = useState(false);
  const [uploadingFile, setUploadingFile] = useState([]);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsUserUploading(true);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    // setIsUserUploading(false); // Reset the isUserUploading state after the file is dropped
    const file = e.dataTransfer.files[0];
    setUploadingFile(file)
  };

  useEffect(() => {
  }, [isUserUploading]);

  return (
    <div className={`app ${isUserUploading ? 'light':'drak'}`}>
      <div
        className="container"
        onDragEnter={handleDrag}
        onDragOver={(e) => e.preventDefault()} // Prevent default to enable the drop event
        onDrop={handleDrop}
      >
        {isUserUploading ? <UploadComponent user={user} file={uploadingFile} setIsUserUploading={setIsUserUploading} /> : <FeedComponent user={user} />}
      </div>
    </div>
  );
}


export default ScrollFeedPage;
