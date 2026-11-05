import { useColorScheme } from 'react-native';

const light = {
  primary: '#2F6B4F', // Fern
  primaryPressed: '#24543E',
  background: '#FBF7EF', // Cream
  surface: '#FFFFFF',
  text: '#1E1E1C',
  textSecondary: '#6B6A65',
  danger: '#B3261E',
  border: '#E6E0D4',
};

const dark: typeof light = {
  primary: '#7FC3A0',
  primaryPressed: '#6AAE8B',
  background: '#151513',
  surface: '#1F1F1C',
  text: '#F4F1EA',
  textSecondary: '#A9A79F',
  danger: '#F2B8B5',
  border: '#33322D',
};

export function useColors() {
  return useColorScheme() === 'dark' ? dark : light;
}

export const spacing = { xs: 4, sm: 8, md: 16, lg: 24, xl: 32 };
export const radii = { sm: 8, md: 12, lg: 20 };

export const type = {
  display: { fontFamily: 'Recoleta-SemiBold', fontSize: 32 },
  title: { fontFamily: 'Recoleta-SemiBold', fontSize: 22 },
  body: { fontSize: 17 },
  caption: { fontSize: 13 },
};
