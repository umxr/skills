// The Leaf Bar: Fernleaf's signature tab bar (see docs/brand.md).
import { Pressable, View, Text, StyleSheet } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import type { BottomTabBarProps } from '@react-navigation/bottom-tabs';
import { Ionicons } from '@expo/vector-icons';
import { useColors, type } from '../theme/tokens';

const ICONS: Record<string, keyof typeof Ionicons.glyphMap> = { Home: 'leaf', Cart: 'bag', Profile: 'person' };

export function BrandTabBar({ state, navigation }: BottomTabBarProps) {
  const colors = useColors();
  const insets = useSafeAreaInsets();
  return (
    <View accessibilityRole="tablist" style={[styles.bar, { paddingBottom: insets.bottom, backgroundColor: colors.surface, borderTopColor: colors.border }]}>
      {state.routes.map((route, index) => {
        const focused = state.index === index;
        const onPress = () => {
          const event = navigation.emit({ type: 'tabPress', target: route.key, canPreventDefault: true });
          if (!focused && !event.defaultPrevented) navigation.navigate(route.name);
        };
        const isCentre = route.name === 'Cart';
        return (
          <Pressable
            key={route.key}
            accessibilityRole="tab"
            accessibilityState={{ selected: focused }}
            accessibilityLabel={route.name}
            onPress={onPress}
            style={[styles.item, isCentre && styles.centre, isCentre && { backgroundColor: colors.primary }]}
          >
            <Ionicons name={ICONS[route.name]} size={24} color={isCentre ? '#FFFFFF' : focused ? colors.primary : colors.textSecondary} />
            {!isCentre && <Text style={[type.caption, { color: focused ? colors.primary : colors.textSecondary }]}>{route.name}</Text>}
          </Pressable>
        );
      })}
    </View>
  );
}

const styles = StyleSheet.create({
  bar: { flexDirection: 'row', borderTopWidth: StyleSheet.hairlineWidth },
  item: { flex: 1, minHeight: 49, alignItems: 'center', justifyContent: 'center' },
  centre: { flex: 0, width: 64, height: 64, borderRadius: 32, marginTop: -20 },
});
