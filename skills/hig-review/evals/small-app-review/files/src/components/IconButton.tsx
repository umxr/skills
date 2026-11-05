import { Pressable, StyleSheet } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useColors } from '../theme/tokens';

type Props = {
  icon: keyof typeof Ionicons.glyphMap;
  onPress: () => void;
};

export function IconButton({ icon, onPress }: Props) {
  const colors = useColors();
  return (
    <Pressable onPress={onPress} style={styles.btn}>
      <Ionicons name={icon} size={18} color={colors.textSecondary} />
    </Pressable>
  );
}

const styles = StyleSheet.create({
  btn: { width: 30, height: 30, alignItems: 'center', justifyContent: 'center' },
});
