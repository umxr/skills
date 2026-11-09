import { TextInput, Text, View, StyleSheet, Alert } from 'react-native';
import { PrimaryButton } from '../components/PrimaryButton';
import { useColors, spacing, radii, type } from '../theme/tokens';

async function placeOrder(email: string) {
  await fetch('https://api.fernleaf.example/orders', { method: 'POST', body: JSON.stringify({ email }) });
}

export function CheckoutScreen() {
  const colors = useColors();
  let email = '';
  return (
    <View style={[styles.root, { backgroundColor: colors.background }]}>
      <Text style={[type.title, { color: colors.text }]}>Checkout</Text>
      <TextInput
        placeholder="Email for receipt"
        onChangeText={(t) => (email = t)}
        style={[styles.input, { borderColor: colors.border, color: colors.text }]}
      />
      <PrimaryButton
        title="Pay £3.70"
        onPress={async () => {
          await placeOrder(email);
          Alert.alert('Success!', 'Your brew is on its way', [{ text: 'OK' }, { text: 'View order' }, { text: 'Share' }, { text: 'Close' }]);
        }}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, padding: spacing.lg, gap: spacing.md },
  input: { borderWidth: 1, borderRadius: radii.sm, padding: spacing.md, fontSize: 17 },
});
