import { Text, View, StyleSheet, Pressable } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useColors, spacing, type } from '../theme/tokens';

export function ProfileScreen() {
  const colors = useColors();
  return (
    <SafeAreaView edges={['top']} style={{ flex: 1, backgroundColor: colors.background }}>
      <Text style={[type.title, styles.heading, { color: colors.text }]}>Profile</Text>
      <View style={styles.list}>
        <Pressable accessibilityRole="button" style={styles.row}>
          <Text style={[type.body, { color: colors.text }]}>Order history</Text>
        </Pressable>
        <Pressable accessibilityRole="button" style={styles.row}>
          <Text style={[type.body, { color: colors.danger }]}>Sign out</Text>
        </Pressable>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  heading: { paddingHorizontal: spacing.md, paddingVertical: spacing.sm },
  list: { paddingHorizontal: spacing.md },
  row: { minHeight: 44, justifyContent: 'center' },
});
