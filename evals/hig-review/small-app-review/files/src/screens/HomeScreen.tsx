import { FlatList, Pressable, Text, View, StyleSheet } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useNavigation } from '@react-navigation/native';
import { useColors, spacing, radii, type } from '../theme/tokens';

const MENU = [
  { id: 'flat-white', name: 'Flat white', price: '£3.40' },
  { id: 'oat-latte', name: 'Oat latte', price: '£3.70' },
  { id: 'cold-brew', name: 'Cold brew', price: '£3.90' },
];

export function HomeScreen() {
  const colors = useColors();
  const navigation = useNavigation<any>();
  return (
    <SafeAreaView edges={['top']} style={{ flex: 1, backgroundColor: colors.background }}>
      <Text style={[type.title, styles.heading, { color: colors.text }]}>Menu</Text>
      <FlatList
        data={MENU}
        keyExtractor={(item) => item.id}
        renderItem={({ item }) => (
          <Pressable
            onPress={() => navigation.navigate('Product', { id: item.id })}
            style={[styles.row, { backgroundColor: colors.surface }]}
          >
            <Text style={[type.body, { color: colors.text }]}>{item.name}</Text>
            <View style={styles.priceBox}>
              <Text allowFontScaling={false} style={[styles.price, { color: colors.textSecondary }]}>
                {item.price}
              </Text>
            </View>
          </Pressable>
        )}
      />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  heading: { paddingHorizontal: spacing.md, paddingVertical: spacing.sm },
  row: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', padding: spacing.md, marginHorizontal: spacing.md, marginBottom: spacing.sm, borderRadius: radii.md },
  priceBox: { height: 20 },
  price: { fontSize: 15 },
});
