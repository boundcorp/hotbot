import * as React from "react";
import * as HomeController from "./_server";
import { Dialog, Menu, MenuButton, MenuItem, MenuItems, Transition, TransitionChild, DialogPanel, DialogTitle, RadioGroup, RadioGroupOption, Radio } from '@headlessui/react';
import { useForm, useFieldArray } from 'react-hook-form';
import { handleFormSubmit } from "@/components/utils";
import { createServerPage } from "@/components/ServerPages";

const HomePage = createServerPage(HomeController);
const Home = () => {

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-4">
        hi
      </div>
    </div>
  );
};

export default HomePage.wraps(Home);
