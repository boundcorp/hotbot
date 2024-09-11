import React, { useEffect } from 'react';
import {useForm} from 'react-hook-form';
import {useServer, LoginForm} from './_server';
import {useServer as useLayout} from "@/pages/_server";
import {handleFormSubmit} from "@/components/utils";
import { toast } from 'react-toastify';

/* Floating center card with a login form*/
export default function LoginPage() {
  const server = useServer();
  const layout = useLayout();
  const form = useForm<{requestBody: LoginForm}>();

  const onLoggedIn = () => {
    toast('you are logged in!');
    setTimeout(() => {
      window.location.pathname = '/';
    }, 3000);
  }

  useEffect(() => {
    if(server.user?.email) {
      onLoggedIn();
    }
  }, [server.user?.email]);
  return (
    <div className={"flex justify-center items-center h-full"}>
      <div className={"w-96 p-4 bg-base-100 rounded-xl"}>
        <h1 className={"text-3xl font-bold text-accent pb-2"}>login</h1>
        <form className={"flex flex-col gap-4"}
              onSubmit={handleFormSubmit(form, server.login, {onSuccess: onLoggedIn})}>
          <input type={"text"} placeholder={"username"}
                 className={"input input-primary"} {...form.register('requestBody.username')}/>
          <input type={"password"} placeholder={"password"}
                 className={"input input-primary"} {...form.register('requestBody.password')}/>
          {form.formState.errors.root?.error &&
              <p className={"text-error"}>{form.formState.errors.root.error.message}</p>}
          <button type={"submit"} className={"btn btn-primary"}>login</button>
        </form>
      </div>
    </div>
  );
}