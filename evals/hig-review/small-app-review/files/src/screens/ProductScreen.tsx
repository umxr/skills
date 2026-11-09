import { Pressable, Text, View, StyleSheet } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useNavigation } from '@react-navigation/native';
import * as Haptics from 'expo-haptics';
import { PrimaryButton } from '../components/PrimaryButton';
import { useColors, spacing, type } from '../theme/tokens';

export function ProductScreen() {
  const colors = useColors();
  const navigation = useNavigation<any>();
  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: colors.background }}>
      <Pressable onPress={() => navigation.goBack()} style={styles.back}>
        <Text style={[type.body, { color: colors.primary }]}>← Back</Text>
      </Pressable>
      <View style={styles.body}>
        <Text style={[type.display, { color: colors.text }]}>Oat latte</Text>
        <Text style={[type.body, { color: colors.textSecondary }]}>Double shot, steamed oat milk.</Text>
      </View>
      <View style={styles.footer}>
        <PrimaryButton
          title="Add to cart"
          color="#FF6B00"
          onPress={() => {
            Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
            navigation.navigate('Main', { screen: 'Cart' });
          }}
        />
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  back: { padding: spacing.md },
  body: { flex: 1, padding: spacing.lg, gap: spacing.md },
  footer: { padding: spacing.lg },
});
