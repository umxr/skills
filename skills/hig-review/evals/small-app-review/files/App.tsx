import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { useState } from 'react';
import { BrandTabBar } from './src/components/BrandTabBar';
import { OnboardingScreen } from './src/screens/OnboardingScreen';
import { HomeScreen } from './src/screens/HomeScreen';
import { ProductScreen } from './src/screens/ProductScreen';
import { CartScreen } from './src/screens/CartScreen';
import { CheckoutScreen } from './src/screens/CheckoutScreen';
import { ProfileScreen } from './src/screens/ProfileScreen';

const Stack = createNativeStackNavigator();
const Tabs = createBottomTabNavigator();

function MainTabs() {
  return (
    <Tabs.Navigator tabBar={(props) => <BrandTabBar {...props} />} screenOptions={{ headerShown: false }}>
      <Tabs.Screen name="Home" component={HomeScreen} />
      <Tabs.Screen name="Cart" component={CartScreen} />
      <Tabs.Screen name="Profile" component={ProfileScreen} />
    </Tabs.Navigator>
  );
}

export default function App() {
  const [onboarded, setOnboarded] = useState(false);
  return (
    <SafeAreaProvider>
      <NavigationContainer linking={{ prefixes: ['fernleaf://'] }}>
        <Stack.Navigator>
          {!onboarded ? (
            <Stack.Screen name="Onboarding" options={{ headerShown: false }}>
              {() => <OnboardingScreen onDone={() => setOnboarded(true)} />}
            </Stack.Screen>
          ) : (
            <>
              <Stack.Screen name="Main" component={MainTabs} options={{ headerShown: false }} />
              <Stack.Screen
                name="Product"
                component={ProductScreen}
                options={{ headerShown: false, gestureEnabled: false }}
              />
              <Stack.Screen name="Checkout" component={CheckoutScreen} options={{ presentation: 'modal' }} />
            </>
          )}
        </Stack.Navigator>
      </NavigationContainer>
    </SafeAreaProvider>
  );
}
