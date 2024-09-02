import React from "react";
import {FieldValues, UseFormReturn} from "react-hook-form";


// We copied this from the server, because its very short, and we want to avoid
// doing relative imports in the client for this simple type
export class FetchErrorBase<T> extends Error {
  statusCode: number;
  body: T;

  constructor(statusCode: number, body: T) {
    super(`Error ${statusCode}: ${body}`);

    this.statusCode = statusCode;
    this.body = body;
  }
}

export interface FormError {
  status_code: number;
  detail: string;
  headers: Record<string, string>;
  field_errors: Record<string, string> | null;
}

export class FormErrorException extends FetchErrorBase<FormError> {
}


export type FormSubmitOptions<R> = {
  onSuccess?: (response: R) => void,
  onFormError?: (e: FormErrorException) => void
  onError?: (e: unknown) => void
}

export function handleFormSubmit<T extends FieldValues, R>(form: UseFormReturn<T>, action: (data: T) => Promise<R>, options?: FormSubmitOptions<R>) {
  return form.handleSubmit(async (values) => {
    try {
      const response = await action(values);
      if (options?.onSuccess) {
        options.onSuccess(response);
      }
    } catch (e) {
      if (e instanceof FetchErrorBase && e.body.detail) {
        console.error("Form Error: ", e.body.detail);
        form.setError("root.error", {message: e.body.detail})
        if (options?.onFormError) {
          options.onFormError(e);
        }
      } else {
        console.error("Unknown Submit Error: ", e);
        if (options?.onError) {
          options.onError(e);
        }
      }
    }
  })
}