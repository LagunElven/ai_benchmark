function createNavigator(initialRoute, canLeave) {
  const stack = [initialRoute];
  return {
    current: () => stack[stack.length - 1],
    history: () => stack,
    async navigate(route) {
      stack.push(route);
      return route;
    },
    async replace(route) {
      stack[stack.length - 1] = route;
      return route;
    },
    async back() {
      if (stack.length > 1) stack.pop();
      return stack[stack.length - 1];
    },
  };
}

module.exports = { createNavigator };
