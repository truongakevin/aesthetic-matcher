import React from 'react';
import { View, Text, TouchableOpacity, Linking, StyleSheet } from 'react-native';

const Features = ({ features }) => {

  return (
    <View style={styles.featuresContainer}>
      {features.map((item, index) => (
        <TouchableOpacity onPress={() => Linking.openURL(`https://aesthetics.fandom.com/wiki/${(item.feature).replace(/\s+/g, '_')}`)}>
          <View key={index} style={[styles.text, styles.feature]}>
            <Text style={[styles.text, styles.itemFeat]}>{item.feature.toLowerCase()}</Text>
            <Text style={[styles.text, styles.itemProb]}>{item.probability}%</Text>
          </View>
        </TouchableOpacity>
      ))}
    </View>
  );
};

const styles = StyleSheet.create({
  text: {
    color: '#000',
    fontFamily: 'Rowdies-Regular',
  },
  featuresContainer: {
    marginHorizontal: 'auto',
    width: '95%',
    marginBottom: 20,
    justifyContent: 'center',
  },
  feature: {
    backgroundColor: '#d0c2d1',
    borderRadius: 10,
    paddingHorizontal: 15,
    paddingVertical: 5,
    flexDirection: 'row',
    margin: 5,
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  itemFeat: {
    color: '#000',
    fontSize: 20,
    textAlign: 'center',
    paddingBottom: 3,
  },
  itemProb: {
    color: '#616161',
    fontSize: 20,
    textAlign: 'center',
  }
});

export default Features;