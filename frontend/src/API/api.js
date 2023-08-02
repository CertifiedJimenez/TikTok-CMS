import axios from 'axios';

class Posts {
    constructor(token) {
      this.token = token;
    }
  
    // Function to fetch Posts
    async getPosts() {
      const token = this.token; 
      try {
        const response = await axios.get('http://127.0.0.1:8000/posts/', {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        });
        return response.data;
      } catch (error) {
        console.error('Error fetching posts:', error);
        return null;
      }
    }

  async uploadPost(file, caption){
    const token = this.token;
    const formData = new FormData();
    formData.append('video', file);
    formData.append('caption', caption);
  
    try {
      const response = await axios.post('http://127.0.0.1:8000/posts/', formData, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'multipart/form-data', // Set the content type to multipart/form-data for file uploads
        },
      });
      return response.data;
    } catch (error) {
      console.error('Error uploading post:', error);
      return null;
    }
    }

}

export default Posts
