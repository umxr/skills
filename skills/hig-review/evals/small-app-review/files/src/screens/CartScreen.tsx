import { FlatList, Text, View, StyleSheet } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useNavigation } from '@react-navigation/native';
import { useState } from 'react';
import { IconButton } from '../components/IconButton';
import { PrimaryButton } from '../components/PrimaryButton';
import { useColors, spacing, type } from '../theme/tokens';

export function CartScreen() {
  const colors = useColors();
  const navigation = useNavigation<any>();
  const [items, setItems] = useState([{ id: '1', name: 'Oat latte', price: '£3.70' }]);
  return (
    <SafeAreaView edges={['top']} style={{ flex: 1, backgroundColor: colors.background }}>
      <Text style={[type.title, styles.heading, { color: colors.text }]}>Your order</Text>
      <FlatList
        data={items}
        keyExtractor={(i) => i.id}
        renderItem={({ item }) => (
          <View style={[styles.row, { backgroundColor: colors.surface }]}>
            <Text style={[type.body, { color: colors.text }]}>{item.name}</Text>
            <IconButton icon="trash-outline" onPress={() => setItems((all) => all.filter((x) => x.id !== item.id))} />
          </View>
        )}
      />
      <View style={styles.footer}>
        <PrimaryButton title="Checkout" onPress={() => navigation.navigate('Checkout')} disabled={items.length === 0} />
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  heading: { paddingHorizontal: spacing.md, paddingVertical: spacing.sm },
  row: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', padding: spacing.md, marginHorizontal: spacing.md },
  footer: { padding: spacing.lg },
});
