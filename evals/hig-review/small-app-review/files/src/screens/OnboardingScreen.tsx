import { View, Text, StyleSheet } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { PrimaryButton } from '../components/PrimaryButton';
import { useColors, spacing, type } from '../theme/tokens';

export function OnboardingScreen({ onDone }: { onDone: () => void }) {
  const colors = useColors();
  return (
    <SafeAreaView style={[styles.root, { backgroundColor: colors.background }]}>
      <View style={styles.body}>
        <Text style={[type.display, { color: colors.text }]}>Good coffee, close by</Text>
        <Text style={[type.body, { color: colors.textSecondary }]}>Order ahead from Fernleaf and skip the line.</Text>
      </View>
      <PrimaryButton title="Get started" onPress={onDone} />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, padding: spacing.lg, justifyContent: 'space-between' },
  body: { gap: spacing.md, marginTop: spacing.xl },
});
