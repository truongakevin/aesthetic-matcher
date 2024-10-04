import React, { useEffect, useState } from 'react';
import { Linking, StyleSheet, Text, View, Image, Platform, ActivityIndicator, TouchableOpacity, ScrollView } from 'react-native';
import * as Font from 'expo-font';
import * as ImagePicker from 'expo-image-picker';
import AHImage from 'react-native-image-auto-height';
import Features from './Features';

async function loadFonts() {
  await Font.loadAsync({
    'Rowdies-Bold': require('./assets/fonts/Rowdies-Bold.ttf'),
    'Rowdies-Regular': require('./assets/fonts/Rowdies-Regular.ttf'),
  });
}

const CustomButton = ({ onPress, title }) => (
  <TouchableOpacity onPress={onPress} style={styles.button}>
    <Text style={styles.buttonText}>{title}</Text>
  </TouchableOpacity>
);

export default function App() {
  const [fontsLoaded, setFontsLoaded] = useState(false);
  const [images, setImages] = useState([]);  // Store multiple images
  const [loading, setLoading] = useState(false);
  const [features, setFeatures] = useState([]);

  useEffect(() => {
    loadFonts().then(() => setFontsLoaded(true));
  }, []);

  const pickImages = async () => {
    let permissionResult = await ImagePicker.requestMediaLibraryPermissionsAsync();
    if (!permissionResult.granted) {
      console.log('Permission required', 'Permission to access camera roll is required!');
      return;
    }

    let result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      allowsMultipleSelection: true,  // Allow multiple selection
      quality: 1,
    });

    if (!result.cancelled) {
      setImages(result.assets.map(asset => asset.uri));  // Store multiple image URIs
    }
  };

  const takePhoto = async () => {
    let permissionResult = await ImagePicker.requestCameraPermissionsAsync();
    if (!permissionResult.granted) {
      console.log('Permission required', 'Permission to access camera is required!');
      return;
    }

    let result = await ImagePicker.launchCameraAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      quality: 1,
    });

    if (!result.cancelled) {
      setImages([...images, result.uri]);  // Append new image to the array
    }
  };

  const uploadImages = async () => {
    setLoading(true);
    try {
      let formData = new FormData();
      
      // Assume images is an array of image URIs
      for (const [index, image] of images.entries()) {
        if (Platform.OS === 'web') {
          let base64Response = await fetch(image);
          let blob = await base64Response.blob();
          formData.append('images', blob, `photo${index}.jpg`);  // Append each image with a unique name
        } else {
          let filename = image.split('/').pop();
          let match = /\.(\w+)$/.exec(filename);
          let type = match ? `image/${match[1]}` : `image`;
          formData.append('images', { uri: image, name: filename, type: type });  // Append each image
        }
      }
      const response = await fetch(`${process.env.NODE_ADDRESS}` || 'http://localhost:5555/analyze-image-am', {
      // const response = await fetch('http://localhost:5555/analyze-image-am', {
        method: 'POST',
        body: formData,
        headers: {
          'Accept': 'application/json',
          // 'Content-Type': 'multipart/form-data', // Uncommenting this can cause issues with FormData
        },
      });    

      if (response.ok) {
        const data = await response.json();
        setFeatures(data);
      } else {
        throw new Error('Failed to upload images');
      }
    } catch (error) {
      alert('Error uploading images: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <ScrollView style={styles.container} contentContainerStyle={{ flexGrow: 1, justifyContent: 'space-between' }}>
      <Text onPress={() => { setImages([]); setFeatures([]); }} style={[styles.text, styles.title]}>aesthetic matcher</Text>
      
      {/* Display multiple images */}
      <View style={styles.imageContainer}>
        {images.map((imageUri, index) => (
          <AHImage key={index} source={{ uri: imageUri }} style={styles.image} />
        ))}
      </View>

      {features.length > 0 && <Features features={features} />}

      <View style={styles.buttonContainer}>
        {!images.length ? (
          <>
            <CustomButton title="take" onPress={takePhoto} />
            <CustomButton title="upload" onPress={pickImages} />
          </>
        ) : (
          <>
            {loading ? (
              <ActivityIndicator size="large" color="#f5d6f5" style={styles.activityIndicator} />
            ) : (
              <>
                <CustomButton title={features.length === 0 ? 'match' : 'retry'} onPress={uploadImages} />
                <CustomButton title="new upload" onPress={() => { setImages([]); setFeatures([]); }} />
              </>
            )}
          </>
        )}
        {features.length > 0 && 
          <>
            <TouchableOpacity
              style={styles.donateButton}
              onPress={() => {Linking.openURL('https://ko-fi.com/truongakevin').catch((err) => console.error('Error opening link', err));}}
            >
              <Text style={styles.buttonText}>donate</Text>
            </TouchableOpacity>
          </>
        }
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  text: {
    color: '#000',
    fontFamily: 'Rowdies-Bold',
  },
  container: {
    backgroundColor: '#161616',
  },
  title: {
    fontSize: 55,
    marginVertical: 25,
    marginTop: 50,
    lineHeight: 40,
    letterSpacing: -1.10,
    textAlign: 'center',
    color: '#d39dd3',
  },
  imageContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'center',
    marginBottom: 20,
  },
  image: {
    width: 300,
    height: 'auto',
    resizeMode: 'contain',
    margin: 10,
    borderRadius: 5,
  },
  activityIndicator: {
    marginBottom: 'auto',
    paddingVertical: 50,
  },
  buttonContainer: {
    flexDirection: 'column',
    justifyContent: 'space-between',
    marginBottom: 50,
  },
  button: {
    paddingVertical: 20,
    paddingHorizontal: 50,
    marginHorizontal: 'auto',
    borderRadius: 50,
    marginBottom: 20,
    alignItems: 'center',
    backgroundColor: '#f5d6f5',
  },
  buttonText: {
    color: '#000',
    fontFamily: 'Rowdies-Regular',
    fontSize: 20,
    fontWeight: 'bold',
  },
  donateButton: {
    marginTop: 30,
    paddingVertical: 15,
    paddingHorizontal: 30,
    marginHorizontal: 'auto',
    borderRadius: 50,
    marginBottom: 20,
    alignItems: 'center',
    backgroundColor: '#fa7d7d',
  },
});