import React from "react";

export function createServerPage<T>({useServer}: {useServer: () => T}) {
  const Context = React.createContext<T | null>(null);
  const useContext = () => React.useContext(Context) as T;
  const Provider = ({ children }: { children: React.ReactNode }) => {
    const serverState = useServer();
    return <Context.Provider value={serverState}>{children}</Context.Provider>;
  };
  const wraps = (Component: React.ComponentType<any>) => (props: any) => (
    <Provider>
      <Component {...props} />
    </Provider>
  );

  return { Context, useContext, Provider, wraps };
}