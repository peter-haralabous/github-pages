import type { Model } from 'survey-core';
import { fetchJson } from '../fetchJson';

const deleteFile = async (url: string, csrfToken: Args['csrfToken']) => {
  const resp = await fetch(url, {
    method: 'DELETE',
    headers: {
      'X-CSRFToken': csrfToken || '',
    },
  });

  if (resp.ok) {
    return 'success';
  }
};

interface Args {
  uploadUrl: string | null;
  deleteUrl: string | null;
  fetchUrl: string | null;
  csrfToken: string | null;
}

export function setupFileUploadInput(survey: Model, args: Args) {
  const { uploadUrl, deleteUrl, fetchUrl, csrfToken } = args;

  survey.onUploadFiles.add(async (_, options) => {
    const formData = new FormData();
    options.files.forEach((file) => {
      console.log('file', { file });
      formData.append('file-upload', file);
    });

    if (!uploadUrl) {
      return;
    }

    try {
      const response = await fetchJson(uploadUrl, {
        method: 'POST',
        body: formData,
        // Override headers to exclude 'Content-Type' so
        // the browser sets the multipart boundary
        headers: {
          'X-CSRFToken': csrfToken || '',
        },
      });
      options.callback(
        options.files.map((file) => {
          const resp = response.find(
            (d: { original_filename: string }) =>
              d.original_filename === file.name,
          );
          return {
            file: file,
            content: resp.url,
            id: resp.id,
          };
        }),
      );
    } catch (error) {
      console.error('Error: ', error);
      options.callback([], ['An error occurred during file upload.']);
    }
  });

  survey.onClearFiles.add(async (_, options) => {
    if (!options.value || options.value.length === 0) {
      return options.callback('success');
    }
    const filesToDelete = options.fileName
      ? options.value.filter((item: File) => item.name === options.fileName)
      : options.value;
    if (filesToDelete.length === 0) {
      console.error(`File with name ${options.fileName} is not found`);
      return options.callback('error');
    }
    const results = await Promise.all(
      filesToDelete.map((file: File) => {
        const url = deleteUrl + `?name=${file.name}`;
        return deleteFile(url, csrfToken);
      }),
    );
    if (results.every((res) => res === 'success')) {
      options.callback('success');
    } else {
      options.callback('error');
    }
  });

  survey.onDownloadFile.add(async (_, options) => {
    try {
      const resp = await fetch(fetchUrl + `?name=${options.fileValue.name}`);
      const blob = await resp.blob();
      const file = new File([blob], options.fileValue.name, {
        type: options.fileValue.type,
      });
      const reader = new FileReader();
      reader.onload = (e) => {
        if (e?.target) {
          options.callback('success', e.target.result);
        }
      };
      reader.readAsDataURL(file);
    } catch (error) {
      console.error('Error: ', error);
      options.callback('error');
    }
  });
}
