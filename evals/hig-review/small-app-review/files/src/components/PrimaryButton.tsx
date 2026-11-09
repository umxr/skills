import { Pressable, Text, StyleSheet } from 'react-native';
import { useColors, radii, type } from '../theme/tokens';

type Props = { title: string; onPress: () => void; disabled?: boolean; color?: string };

export function PrimaryButton({ title, onPress, disabled, color }: Props) {
  const colors = useColors();
  return (
    <Pressable
      accessibilityRole="button"
      onPress={onPress}
      disabled={disabled}
      style={({ pressed }) => [
        styles.btn,
        { backgroundColor: color ?? (pressed ? colors.primaryPressed : colors.primary), opacity: disabled ? 0.5 : 1 },
      ]}
    >
      <Text style={[type.body, styles.label]}>{title}</Text>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  btn: { minHeight: 50, borderRadius: radii.md, alignItems: 'center', justifyContent: 'center', paddingHorizontal: 20 },
  label: { color: '#FFFFFF', fontWeight: '600' },
});
