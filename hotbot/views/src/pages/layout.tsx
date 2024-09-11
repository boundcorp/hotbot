import React from "react"
import { createServerPage } from "@/components/ServerPages";

import { ToastContainer} from 'react-toastify';
import { useServer } from "@/pages/_server";
import * as LayoutController from "./_server";

import { Menu, MenuButton, MenuItems, MenuItem } from '@headlessui/react';

export const LayoutPage = createServerPage(LayoutController);

export default function Layout({ children }: { children: React.ReactNode }) {
    return (
        <LayoutPage.Provider>
            <ToastContainer />
            {children}
        </LayoutPage.Provider>
    );
}